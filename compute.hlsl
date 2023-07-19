cbuffer Config : register(b0)
{
    int4 offset;
};

float rng(int2 pos)
{ // bad rng but idc
	float combo = float(pos.x) * float(offset.z) + float(pos.y) * 127;
	return abs(combo % 2 - 1);
}

/*

config:
    offset.xy = xy
	offset.z = rng

inf_array:
    density f32

inf_array:
    type u32

reactions:
    product arr<vec2<u32>>

world:
    mat_ids arr<u32>
*/

// 8 material types in a 65x65
RWTexture2D<uint> world : register(u0); // rw
Texture1D<uint> type : register(t0); // r
Texture1D<float> density : register(t1); // r
Texture2D<uint> react_pair_reactant : register(t2); // r
Texture2D<uint> react_pair_catalyst : register(t3); // r
Texture2D<float> react_pair_prob : register(t4); // r

[numthreads(8,8,1)]
void main(int3 global_pos : SV_DispatchThreadID)
{
    int2 pos = global_pos.xy * 3 + offset.xy;
    // if 2 sand pixels are 1 space apart they made randomly fall into the same spot for *2 causing matter deletion

	// init
	uint c_mat = world[pos];
	bool dir;
	uint swap;
	float sampleL;
	float sampleR;
	bool freeR = pos.x + 1 < 1/*$WIDTH*/;
	bool freeL = pos.x > 0;
	bool freeU = pos.y > 0;
	bool freeD = pos.y + 1 < 1/*$HEIGHT*/;
    if (react_pair_prob[int2(3, 1)] > 0.5) { world[pos] = 0;}
    if (react_pair_prob[int2(1, 3)] > 0.5) { world[pos] = 0;}
	// react
	int rand = int(rng(int2(pos.x+20,pos.y+7)) * 4.0); // 0..4 truncates to i(0..=3)
	int2 second_pos = int2(pos.x+(rand%2)*2-1,pos.y+(rand/2)*2-1);
	uint s_mat = world[second_pos];
	int2 pair = int2(c_mat,s_mat);
	// if n_mat+1 == 0 // we don't need this because p = 0
	if (rng(int2(pos.x-4,pos.y+32)) < react_pair_prob[pair])
	{
		world[pos] = react_pair_reactant[pair];
		world[second_pos] = react_pair_catalyst[pair];
		c_mat = world[pos];
	}

	// physics
    switch (type[c_mat])
    {
        case 0: // air
            return;
        case 1: // gas
			// U / D < > flip gas
            if (!freeU)
            { // top of world
                return;
            }
            swap = world[int2(pos.x,pos.y-1)];
            if (density[swap] > density[c_mat])
            { // float
                world[int2(pos.x,pos.y-1)] = world[pos];
                world[pos] = swap;
				return;
            }
			dir = rng(pos) > 0.5;
			swap = world[int2(pos.x + int(dir) * 2 - 1,pos.y-1)];
			if(density[swap] > density[c_mat])
			{ // slide
				if ((dir && !freeR) || (!dir && !freeL)) {return;}
				world[int2(pos.x + int(dir) * 2 - 1,pos.y-1)] = world[pos];
                world[pos] = swap;
				return;
			}
			// flowing stuff
			sampleL = density[world[int2(pos.x-1,pos.y)]]; // get LR
			sampleR = density[world[int2(pos.x+1,pos.y)]];
			if (abs(sampleL-sampleR) < 0.01) // same mat
			{
				if ((dir && !freeR) || (!dir && !freeL)) {return;}
				swap = world[int2(pos.x + int(dir) * 2 - 1,pos.y)];
				if(density[swap] > density[c_mat])
				{
					// flow
					world[int2(pos.x + int(dir) * 2 - 1,pos.y)] = world[pos];
					world[pos] = swap;
				}
				return;
			}
			if (sampleL < sampleR)
			{
				// right is easier
				if (!freeR) {return;}
				swap = world[int2(pos.x + 1,pos.y)];
				world[int2(pos.x + 1,pos.y)] = world[pos];
				world[pos] = swap;
				return;
			}
			if (sampleR < sampleL)
			{
				// left is easier
				if (!freeL) {return;}
				swap = world[int2(pos.x - 1,pos.y)];
				world[int2(pos.x - 1,pos.y)] = world[pos];
				world[pos] = swap;
				return;
			}
            return;
        case 2: // sand
            if (!freeD)
            { // bottom of world
                return;
            }
            swap = world[int2(pos.x,pos.y+1)];
            if (density[swap] < density[c_mat])
            { // fall
                world[int2(pos.x,pos.y+1)] = world[pos];
                world[pos] = swap;
				return;
            }
			dir = rng(pos) > 0.5;
			swap = world[int2(pos.x + int(dir) * 2 - 1,pos.y+1)];
			if(density[swap] < density[c_mat])
			{ // slide
				if ((dir && !freeR) || (!dir && !freeL)) {return;}
				world[int2(pos.x + int(dir) * 2 - 1,pos.y+1)] = world[pos];
                world[pos] = swap;
				return;
			}
            return;
		case 3: // liquid
			if (!freeD)
            { // bottom of world
                return;
            }
            swap = world[int2(pos.x,pos.y+1)];
            if (density[swap] < density[c_mat])
            { // fall
                world[int2(pos.x,pos.y+1)] = world[pos];
                world[pos] = swap;
				return;
            }
			dir = rng(pos) > 0.5;
			swap = world[int2(pos.x + int(dir) * 2 - 1,pos.y+1)];
			if(density[swap] < density[c_mat])
			{ // slide
				if ((dir && !freeR) || (!dir && !freeL)) {return;}
				world[int2(pos.x + int(dir) * 2 - 1,pos.y+1)] = world[pos];
                world[pos] = swap;
				return;
			}
			// flowing stuff
			sampleL = density[world[int2(pos.x-1,pos.y)]]; // get LR
			sampleR = density[world[int2(pos.x+1,pos.y)]];
			if (abs(sampleL-sampleR) < 0.01) // same mat
			{
				if ((dir && !freeR) || (!dir && !freeL)) {return;}
				swap = world[int2(pos.x + int(dir) * 2 - 1,pos.y)];
				if(density[swap] < density[c_mat])
				{
					// flow
					world[int2(pos.x + int(dir) * 2 - 1,pos.y)] = world[pos];
					world[pos] = swap;
				}
				return;
			}
			if (sampleL > sampleR)
			{
				// right is easier
				if (!freeR) {return;}
				swap = world[int2(pos.x + 1,pos.y)];
				world[int2(pos.x + 1,pos.y)] = world[pos];
				world[pos] = swap;
				return;
			}
			if (sampleR > sampleL)
			{
				// left is easier
				if (!freeL) {return;}
				swap = world[int2(pos.x - 1,pos.y)];
				world[int2(pos.x - 1,pos.y)] = world[pos];
				world[pos] = swap;
				return;
			}
            return;
		case 4: // solid
			return;
    }
}
